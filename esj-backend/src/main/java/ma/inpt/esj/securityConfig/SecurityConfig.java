package ma.inpt.esj.securityConfig;

import com.nimbusds.jose.jwk.source.ImmutableSecret;
import lombok.RequiredArgsConstructor;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import org.springframework.http.HttpMethod;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.ProviderManager;
import org.springframework.security.authentication.dao.DaoAuthenticationProvider;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.oauth2.jose.jws.MacAlgorithm;
import org.springframework.security.oauth2.jwt.JwtDecoder;
import org.springframework.security.oauth2.jwt.JwtEncoder;
import org.springframework.security.oauth2.jwt.NimbusJwtDecoder;
import org.springframework.security.oauth2.jwt.NimbusJwtEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import javax.crypto.spec.SecretKeySpec;
import java.util.List;

@Configuration
//@EnableWebSecurity
//@EnableMethodSecurity(prePostEnabled = true)
@RequiredArgsConstructor
public class SecurityConfig {
    private final MedecinDetailsService medecinDetailsService;
    private final ProfessionelSanteDetailsService professionelSanteDetailsService;
    private final JeuneDetailsService jeuneDetailsService;
    private final AdminDetailsService adminDetailsService;

    @Value("${ip.address.frontend}")
    private String ipAdressFrontend;

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity httpSecurity) throws Exception{
        return httpSecurity
                .sessionManagement(sm->sm.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                .csrf(csrf->csrf.disable())
                .cors(Customizer.withDefaults())
                .requiresChannel(channel -> channel.anyRequest().requiresSecure()) // Enforce HTTPS
                .authorizeHttpRequests(ar -> ar
                /////////////////////////////////////////////////////
                        .requestMatchers(HttpMethod.OPTIONS, "/**").permitAll()
                        .requestMatchers("/responsables/**").permitAll()
                        // .requestMatchers("/admins/**").permitAll() //added then commented for testing purposes
                        // .requestMatchers("/streams/**").permitAll() //added then commented for testing purposes
                        ///////////////////////////////////////////////
                        .requestMatchers("/auth/login/**").permitAll()
                        .requestMatchers("/register/**").permitAll()
                        .requestMatchers("/password/**").permitAll()
                        .requestMatchers("/uploads/**").permitAll()
                        .requestMatchers("/validator/**").permitAll()
                         .requestMatchers("/jeunes/**").permitAll()    //added then commented for testing purposes
                        .requestMatchers(
                                "/swagger-ui/**",
                                "/v2/api-docs",
                                "/swagger-resources/**",
                                "/swagger-ui.html",
                                "/webjars/**",
                                "/v3/api-docs/**"
                        ).permitAll()
                        .requestMatchers("/ws/**").permitAll()
                        .anyRequest().authenticated()
                )
                .oauth2ResourceServer(oa->oa.jwt(Customizer.withDefaults()))
                .build();
    }

    @Bean
    @Primary
    public AuthenticationManager authenticationManagerMedecin(){
        DaoAuthenticationProvider daoAuthenticationProvider = new DaoAuthenticationProvider();
        daoAuthenticationProvider.setPasswordEncoder(passwordEncoder());
        daoAuthenticationProvider.setUserDetailsService(medecinDetailsService);
        return new ProviderManager(daoAuthenticationProvider);
    }

    @Bean
    public AuthenticationManager authenticationManagerProfessionelSante(){
        DaoAuthenticationProvider daoAuthenticationProvider = new DaoAuthenticationProvider();
        daoAuthenticationProvider.setPasswordEncoder(passwordEncoder());
        daoAuthenticationProvider.setUserDetailsService(professionelSanteDetailsService);
        return new ProviderManager(daoAuthenticationProvider);

    }

    @Bean
    public AuthenticationManager authenticationManagerJeune(){
        DaoAuthenticationProvider daoAuthenticationProvider = new DaoAuthenticationProvider();
        daoAuthenticationProvider.setPasswordEncoder(passwordEncoder());
        daoAuthenticationProvider.setUserDetailsService(jeuneDetailsService);
        return new ProviderManager(daoAuthenticationProvider);

    }
    @Bean
    public AuthenticationManager authenticationManagerAdmin() {
        DaoAuthenticationProvider daoAuthenticationProvider = new DaoAuthenticationProvider();
        daoAuthenticationProvider.setPasswordEncoder(passwordEncoder());
        daoAuthenticationProvider.setUserDetailsService(adminDetailsService);
        return new ProviderManager(daoAuthenticationProvider);
    }

    @Bean
    JwtEncoder jwtEncoder() {
        String secretKey = "9faa372517ac1d389758d3750fc07acf00f542277f26fec1ce4593e93f64e338";
        return new NimbusJwtEncoder(new ImmutableSecret<>(secretKey.getBytes()));
    }

    @Bean
    JwtDecoder jwtDecoder() {
        String secretKey = "9faa372517ac1d389758d3750fc07acf00f542277f26fec1ce4593e93f64e338";
        SecretKeySpec secretKeySpec = new SecretKeySpec(secretKey.getBytes(), "HmacSHA512");
        return NimbusJwtDecoder.withSecretKey(secretKeySpec).macAlgorithm(MacAlgorithm.HS512).build();
    }

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration corsConfiguration = new CorsConfiguration();
        corsConfiguration.addAllowedOrigin(ipAdressFrontend);  // Allow requests from your frontend
        corsConfiguration.addAllowedMethod("GET");
        corsConfiguration.addAllowedMethod("POST");
        corsConfiguration.addAllowedMethod("PUT");
        corsConfiguration.addAllowedMethod("DELETE");
        corsConfiguration.addAllowedMethod("PATCH");
        corsConfiguration.addAllowedMethod("OPTIONS");  // Ensure OPTIONS method is allowed
        corsConfiguration.addAllowedHeader("*");  // Allow all headers
        corsConfiguration.setExposedHeaders(List.of("x-auth-token", "Authorization"));  // Allow these headers to be exposed to the frontend
        corsConfiguration.setAllowCredentials(true);  // Allow credentials (cookies, authorization headers)
        
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", corsConfiguration);

        return source;
    }

}
